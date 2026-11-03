int main() {
  int values[24]; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-1-6]
  return static_cast<int>(sizeof(values));
}
