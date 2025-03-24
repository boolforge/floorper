# Roadmap and Pending Tasks

## High Priority
- [ ] **Backup Encryption**  
  `Status:` Pending  
  `Assigned to:` Security Team  
  `Dependencies:` Encryption library (e.g., cryptography)

- [ ] **Plugin System**  
  `Status:` In Design  
  `Assigned to:` Architecture Team  
  `Dependencies:` Core refactoring

## Medium Priority
- [ ] **Cloud Sync**  
  `Status:` Researching  
  `Assigned to:` Cloud Team  
  `Dependencies:` Cloud provider APIs

- [ ] **Remote Migration**  
  `Status:` Specifying  
  `Assigned to:` Networking Team  
  `Dependencies:` Auth module

## Performance Improvements
- [ ] Memory optimization for large migrations  
- [ ] Implement backup compression  
- [ ] Upgrade cache system with LRU

## New Features
- [ ] Browser extension for profile management  
- [ ] Retro browser support (Netscape, IE)  
- [ ] Integration with external password managers

## Maintenance
- [ ] Update Textual and PyQt6 dependencies  
- [ ] Improve test coverage to 95%  
- [ ] Document internal API

## External Dependencies
| Library         | Current Version | Latest Version | Required Action |
|-----------------|-----------------|----------------|-----------------|
| cryptography    | 3.4.7           | 42.0.4         | Update          |
| textual         | 0.1.18          | 0.15.1         | Refactor        |
| PyQt6           | 6.4.2           | 6.6.0          | Test compatibility |

## Legend
🟢 In Progress  
🟡 Pending Review  
🔴 Blocked  
⚪ Not Started
