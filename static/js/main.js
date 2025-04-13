// Add this at the beginning of your app entry.
import '@/css/main.css';
import htmx from 'htmx.org';
import Alpine from 'alpinejs'
 
window.Alpine = Alpine
 
Alpine.start()

window.htmx = htmx; // Make htmx available globally


import { sayHello } from './important';

console.log('main.js loaded');
sayHello('Victor');