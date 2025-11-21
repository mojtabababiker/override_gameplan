const fs = require('fs-extra')
const path = require('path')
const { execSync } = require('child_process')

const gameplanAppPath = path.resolve(__dirname, '../../gameplan/frontend')
const overrideSrcPath = path.resolve(__dirname, './src')
const overrideFilesPath = path.resolve(__dirname, './src_override')

console.log({ gameplanAppPath, overrideSrcPath, overrideFilesPath }, '\n\n')

console.log('Starting  :  Copying original src.')
console.log(`Copying from ${path.join(gameplanAppPath, 'src')} to ${overrideSrcPath}`)
fs.copySync(path.join(gameplanAppPath, 'src'), overrideSrcPath)
console.log('Completed :  Copying original src.')

console.log('Starting  :  Overriding src.')
console.log(`Copying from ${overrideFilesPath} to ${overrideSrcPath}`)
fs.copySync(overrideFilesPath, overrideSrcPath)
console.log('Completed :  Overriding src.')

execSync('pnpm install', { stdio: 'inherit' })
