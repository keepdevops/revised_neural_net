# Stock Prediction GUI - PlantUML Diagrams

This directory contains comprehensive PlantUML diagrams that document the architecture, flow, and structure of the Stock Prediction Neural Network GUI application.

## Diagram Files

### 1. `stock_prediction_gui_flow_diagram.puml`
**Type**: Flow Diagram / Architecture Overview  
**Purpose**: Shows the overall system architecture and component relationships

**Key Features**:
- Main application components and their relationships
- Core managers (DataManager, ModelManager, etc.)
- Integration layer (TrainingIntegration, PredictionIntegration)
- UI panels and specialized components
- External dependencies and data flow
- Threading architecture
- Application lifecycle notes

**Use Cases**:
- Understanding the overall system architecture
- Identifying component dependencies
- Planning modifications or extensions
- Onboarding new developers

### 2. `stock_prediction_gui_sequence_diagram.puml`
**Type**: Sequence Diagram  
**Purpose**: Shows detailed user interaction flows and system interactions

**Key Features**:
- Complete user journey from startup to cleanup
- Data loading and feature selection flow
- Training process with live plotting
- Model selection and prediction flow
- 3D visualization interactions
- Thread-safe UI updates
- Error handling and recovery

**Use Cases**:
- Understanding user workflows
- Debugging interaction issues
- Planning new features
- Testing scenario planning

### 3. `stock_prediction_gui_component_diagram.puml`
**Type**: Component Diagram  
**Purpose**: Shows detailed component structure with interfaces and attributes

**Key Features**:
- Detailed component attributes and methods
- Interface definitions
- Package organization
- External library dependencies
- Component responsibilities
- State management details

**Use Cases**:
- Detailed system understanding
- Interface design
- Component refactoring
- API documentation

### 4. `stock_prediction_gui_deployment_diagram.puml`
**Type**: Deployment Diagram  
**Purpose**: Shows file structure, dependencies, and runtime environment

**Key Features**:
- File organization and dependencies
- Python environment requirements
- Runtime thread management
- Configuration file structure
- Model directory organization
- Data file handling

**Use Cases**:
- Deployment planning
- Environment setup
- File organization
- Dependency management

## How to Use These Diagrams

### Prerequisites
1. **PlantUML Installation**:
   ```bash
   # Install PlantUML (Java required)
   # Download from: http://plantuml.com/download
   
   # Or use VS Code extension
   # Install "PlantUML" extension by jebbs
   ```

2. **Viewing Options**:
   - **VS Code**: Install PlantUML extension and open `.puml` files
   - **Online**: Use http://www.plantuml.com/plantuml/uml/
   - **Command Line**: Use PlantUML jar file
   - **IDE Plugins**: Most IDEs have PlantUML support

### Generating Images
```bash
# Command line (requires PlantUML jar)
java -jar plantuml.jar stock_prediction_gui_flow_diagram.puml
java -jar plantuml.jar stock_prediction_gui_sequence_diagram.puml
java -jar plantuml.jar stock_prediction_gui_component_diagram.puml
java -jar plantuml.jar stock_prediction_gui_deployment_diagram.puml

# This will generate PNG files
```

### VS Code Integration
1. Install PlantUML extension
2. Open any `.puml` file
3. Press `Alt+Shift+P` and select "PlantUML: Preview Current Diagram"
4. Or right-click and select "Preview Current Diagram"

## Diagram Key Concepts

### Architecture Patterns
- **MVC-like Pattern**: Separation of UI, business logic, and data
- **Manager Pattern**: Centralized management of resources
- **Integration Pattern**: Clean separation of external systems
- **Observer Pattern**: Event-driven updates via callbacks

### Thread Safety
- **GUI Thread**: All UI updates via `after_idle()`
- **Background Threads**: Training, prediction, and plotting
- **Thread Communication**: Callback-based progress updates
- **Resource Management**: Proper cleanup and state management

### Data Flow
- **Data Loading**: Multi-format support with validation
- **Feature Selection**: Interactive column selection and locking
- **Training**: Background processing with live visualization
- **Prediction**: Model loading with forward pass visualization
- **Results**: Export and visualization capabilities

### Error Handling
- **Validation**: Parameter and data validation at multiple levels
- **Recovery**: Graceful degradation and error recovery
- **Logging**: Comprehensive logging for debugging
- **User Feedback**: Clear error messages and status updates

## Customization and Extension

### Adding New Components
1. Update the appropriate diagram file
2. Add component definition with attributes and methods
3. Define relationships with existing components
4. Update sequence flows if needed
5. Document in this README

### Modifying Existing Components
1. Update component definitions in diagrams
2. Update relationship arrows
3. Update sequence flows
4. Update deployment structure if needed
5. Regenerate diagrams

### Best Practices
- Keep diagrams focused and readable
- Use consistent naming conventions
- Include relevant notes and documentation
- Update diagrams when code changes
- Use color coding for different component types
- Include error handling and edge cases

## Troubleshooting

### Common Issues
1. **PlantUML not rendering**: Check Java installation
2. **Missing dependencies**: Ensure all required libraries are installed
3. **Large diagrams**: Consider splitting into smaller diagrams
4. **Performance**: Use appropriate diagram types for the use case

### Diagram Maintenance
- Update diagrams when code changes
- Keep diagrams synchronized with implementation
- Use version control for diagram files
- Document significant changes
- Review diagrams regularly for accuracy

## Related Documentation

- `README.md`: Main project documentation
- `GUI_LAUNCH_INSTRUCTIONS.md`: How to run the GUI
- `STOCK_GUI_USER_MANUAL.py`: User manual
- `MIGRATION_GUIDE.md`: Migration and setup guide

## Contributing

When contributing to the project:
1. Update relevant diagrams if architecture changes
2. Add new diagrams for new features
3. Keep diagrams accurate and up-to-date
4. Document changes in this README
5. Use consistent PlantUML syntax and styling

---

**Note**: These diagrams are living documentation and should be updated as the codebase evolves. They serve as both documentation and design tools for the Stock Prediction GUI application. 