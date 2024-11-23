import { execSync } from 'child_process';
import path from 'path';
import { fileURLToPath } from 'url';
import os from 'os';

// 获取 __dirname 等价物
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// conda 环境名称
const CONDA_ENV_NAME = 'fastapi';

try {
  // 获取操作系统相关信息
  const isWindows = os.platform() === 'win32';
  
  // 构建激活conda环境的命令
  const activateCommand = isWindows 
    ? `@call conda activate ${CONDA_ENV_NAME} && ` 
    : `source activate ${CONDA_ENV_NAME} && `;
    
  // 构建执行Python脚本的完整命令
  const buildCommand = isWindows
    ? `${activateCommand} python "${path.join(__dirname, '../build.py')}"`
    : `${activateCommand} python "${path.join(__dirname, '../build.py')}"`;

  // 执行命令
  console.log('Executing build script with conda environment...');
  execSync(buildCommand, {
    stdio: 'inherit',
    shell: isWindows ? 'cmd.exe' : '/bin/bash'
  });
  
  console.log('Python build completed successfully');
} catch (error) {
  console.error('Error during Python build:', error);
  process.exit(1);
} 