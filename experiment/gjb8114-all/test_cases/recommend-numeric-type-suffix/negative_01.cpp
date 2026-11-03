unsigned int getUnsignedValue() {
  unsigned int ucV = 1; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-8-4]
  return ucV;
}
