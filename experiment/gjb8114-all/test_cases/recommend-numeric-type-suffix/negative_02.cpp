float getFloatValue() {
  float fV = 1.0; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-8-4]
  return fV;
}
