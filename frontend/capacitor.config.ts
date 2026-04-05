import { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'com.veloraai.app',
  appName: 'Velora AI',
  webDir: 'dist',
  server: {
    // Allow cleartext (http) traffic to the backend on the local network
    cleartext: true,
    androidScheme: 'http',
  },
  android: {
    allowMixedContent: true,
  },
};

export default config;
