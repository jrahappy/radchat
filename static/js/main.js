// Add this at the beginning of your app entry.
import '@/css/main.css';
// import 'vite/modulepreload-polyfill';
import { sayHello } from './important';

console.log('main.js loaded');
sayHello('Victor');