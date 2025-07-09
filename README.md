# Config Matrix

Config Matrix is a CLI-based application designed to help manage computer setups using profiles and setup steps. This tool is intended for streamlining the process of configuring multiple computers by automating the application of predefined steps and profiles.

## Use Cases

- **Development Environment Setup**: Standardize dev environment configurations across team members.
- **IT Deployment**: Manage computer setup procedures for new employees or hardware.
- **System Administration**: Track software installation and configuration tasks
- **Personal Computer Management**: Organize setup steps for personal devices or family computers

## Features

- **Profile Management**: Create and manage profiles to group related setup steps.
- **Setup Steps**: Define individual setup tasks, which may include instructions or download links.
- **Computer Tracking**: Create computers with assigned profiles to track setup progress.
- **Interactive CLI**: User-friendly command-line interface to manage operations efficiently.

## Technical Stack

- **Language**: Python 3
- **Database**: SQLite with SQLAlchemy ORM
- **Interface**: Interactive command-line interface
- **Architecture**: Modular design with separate modules for profiles, steps, computers, and database management

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/config-matrix.git
   cd config-matrix
   ```

2. Set up a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the CLI:
```bash
python3 cli.py
```

### Main Commands
- `profiles`: Manage setup profiles
- `steps`: Manage setup steps
- `computers`: Manage computers and track progress
- `help`: Show the help menu
- `exit`: Exit the application

### Workflow Overview
1. **Create setup steps**: Use `steps -> new` to define setup tasks.
2. **Create profiles**: Assign steps using `profiles -> new`, `profiles -> toggle`.
3. **Manage computers**: Add computers with profiles and track progress using `computers` commands.

### Tips
- Type `help` in any submenu for specific commands.
- Use `exit` to return to previous menu levels.

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests.

## License

This project is licensed under the Apache License 2.0 – see the [LICENSE](LICENSE) file for details.
