int main() {
  auto const value = 42; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-2-9-2]
  return value == 42 ? 0 : 1;
}
