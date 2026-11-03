int main() {
  int first = 1, second; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-11-1]
  second = 2;
  return first + second;
}
