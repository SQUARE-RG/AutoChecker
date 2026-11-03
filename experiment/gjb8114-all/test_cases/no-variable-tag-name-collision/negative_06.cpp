using Number = int;

int main()
{
  int Number = 0; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-4]
  Number = 42;
  return Number;
}
