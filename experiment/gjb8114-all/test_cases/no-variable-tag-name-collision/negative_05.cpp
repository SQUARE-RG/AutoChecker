union DATA
{
  int i;
  double d;
};

int main()
{
  union DATA DATA; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-4]
  DATA.i = 1;
  return 0;
}
