# Herald Echo

Configure periodic announcements with intelligent message scheduling.

## Overview

Herald Echo is a scheduler service that sends periodic messages to webhooks using a priority queue system. Instead of simple timers, it uses coefficients to control message frequency and ensures intelligent message distribution.

## Features

- **Priority Queue Scheduling**: Messages are dispatched based on calculated priorities
- **Coefficient-based Frequency Control**: Control how often messages appear with coefficient values
- **Message Identification**: Messages are identified by their first 20 characters
- **Webhook Integration**: Send messages to any webhook endpoint
- **Docker Support**: Full containerization with testing support

## Configuration

The configuration is stored in `config.json` as an array of scheduler configurations, allowing multiple parallel schedulers:

```json
[
  {
    "name": "discord_announcements",
    "period": 3600,
    "webhook": "https://discord.com/api/webhooks/your-webhook-url",
    "messages": [
      {
        "content": "Regular hourly message",
        "coefficient": 1.0
      },
      {
        "content": "Less frequent message",
        "coefficient": 0.5
      },
      {
        "content": "More frequent message",
        "coefficient": 2.0
      }
    ]
  },
  {
    "name": "quick_updates",
    "period": 900,
    "webhook": "https://discord.com/api/webhooks/your-webhook-url",
    "messages": [
      {
        "content": "Quick status update",
        "coefficient": 1.0
      },
      {
        "content": "System health check",
        "coefficient": 1.5
      }
    ]
  }
]
```

### Configuration Fields

Each scheduler object contains:
- `name`: Unique identifier for the scheduler (used in logs)
- `period`: Interval in seconds between message dispatches for this scheduler
- `webhook`: Target webhook URL for message delivery
- `messages`: Array of message objects
  - `content`: The message text to send
  - `coefficient`: Frequency multiplier (default: 1.0)
    - Values > 1.0: Message appears more frequently
    - Values < 1.0: Message appears less frequently

### Multiple Schedulers

You can run multiple schedulers simultaneously, each with their own:
- Independent timing periods
- Different webhook endpoints
- Separate message pools
- Individual priority queues

This allows for complex messaging patterns like:
- Hourly announcements to one channel
- Quick updates every 15 minutes to another channel
- Different message frequencies within each scheduler

## Running the Application

### Using nerdctl (recommended)

Build and run the application:

```bash
nerdctl compose build
nerdctl compose up
```

### Using Docker Compose

```bash
docker-compose build
docker-compose up
```

## Testing

### Running Tests

To run the test suite using Docker:

```bash
nerdctl compose -f docker-compose.test.yml build
nerdctl compose -f docker-compose.test.yml up
```

Or with docker-compose:

```bash
docker-compose -f docker-compose.test.yml build
docker-compose -f docker-compose.test.yml up
```

## Development

### Project Structure

```
heraldecho/
├── heraldecho/           # Main application package
│   ├── __init__.py
│   ├── constants.py      # Configuration constants
│   ├── main.py          # Application entrypoint
│   └── models.py        # Core scheduler and message classes
├── tests/               # Test suite
│   ├── __init__.py
│   ├── test_main.py     # Main module tests
│   └── test_models.py   # Models module tests
├── config.json          # Scheduler configuration
├── Dockerfile           # Production container
├── Dockerfile.test      # Testing container
├── docker-compose.yml   # Production compose
├── docker-compose.test.yml # Testing compose
└── pyproject.toml       # Python dependencies
```

### How the Multi-Scheduler Works

1. **Initialization**: Each scheduler loads its messages into independent priority queues
2. **Parallel Processing**: The main loop checks each scheduler independently
3. **Priority Calculation**: For each scheduler, message priority is calculated based on:
   - Time since last sent
   - Message coefficient
   - Random jitter for fairness
4. **Message Selection**: Each scheduler selects its highest priority message when its period elapses
5. **Independent Timing**: Schedulers operate on their own timers without interfering with each other
6. **Queue Update**: After sending, messages are reinserted with updated priorities per scheduler

### Adding New Messages

Edit `config.json` and restart the service.

## Migration from Old Format

The old configuration format used individual `frequency`, `hook`, `message`, and `tag` fields for each job. The new format uses an array of schedulers, each with multiple messages.

Old format:
```json
[
  {
    "frequency": 3200,
    "hook": "https://webhook.url",
    "message": "Message text 1",
    "tag": "identifier 1"
  },
  {
    "frequency": 3200,
    "hook": "https://webhook.url",
    "message": "Message text 2",
    "tag": "identifier 2"
  }
]
```

New format:
```json
[
  {
    "name": "migrated_scheduler",
    "period": 3200,
    "webhook": "https://webhook.url",
    "messages": [
      {
        "content": "Message text 1",
        "coefficient": 1.0
      },
      {
        "content": "Message text 2",
        "coefficient": 1.0
      }
    ]
  }
]
```

To migrate multiple old jobs to a single scheduler, group them by webhook and timing preferences.
