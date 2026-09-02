import { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'com.moneylens.ai',
  appName: 'MoneyLens AI',
  webDir: 'dist',
  server: {
    androidScheme: 'https'
  }
};

export default config;
