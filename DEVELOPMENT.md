# DEVELOPMENT.md

## Local Development Setup
1. **Clone the Repository**  
   ```bash  
   git clone https://github.com/divineearthly/Krishi-Veda-Module.git  
   cd Krishi-Veda-Module  
   ```  
2. **Install Dependencies**  
   Make sure you have [Node.js](https://nodejs.org/) installed. Then run:  
   ```bash  
   npm install  
   ```  

## Architecture Overview
The Krishi Veda Module is structured into the following main components:
- **API Layer**: Responsible for handling requests and responses.
- **Service Layer**: Contains business logic.
- **Data Layer**: Handles data storage and retrieval.
  
Each layer interacts with the others to serve the application's purpose efficiently.

## Testing
To run the test suite, execute the following command:  
```bash  
npm test  
```  
Tests are located in the `__tests__` directory.

## Docker Deployment
1. **Install Docker**: Make sure you have [Docker](https://www.docker.com/) installed on your machine.
2. **Build the Docker Image**:  
   ```bash  
   docker build -t krishi-veda-module .  
   ```  
3. **Run the Container**:  
   ```bash  
   docker run -p 3000:3000 krishi-veda-module  
   ```  

## Debugging Tips
- Use `console.log()` statements during development to track variable states.
- Utilize the built-in debugger in your IDE (like Visual Studio Code).
- Check logs for errors and warnings to diagnose problems quickly.

## Contribution Workflow
1. **Fork the Repository**: Click on the `Fork` button to create your copy of the repository.
2. **Create a New Branch**:  
   ```bash  
   git checkout -b feature-branch-name  
   ```  
3. **Make Your Changes**: Edit files, add features, or fix bugs.
4. **Commit Your Changes**:  
   ```bash  
   git commit -m "Descriptive message of what you did"  
   ```  
5. **Push to Your Fork**:  
   ```bash  
   git push origin feature-branch-name  
   ```  
6. **Create a Pull Request**: Go to the original repository and create a new pull request.

Happy coding!