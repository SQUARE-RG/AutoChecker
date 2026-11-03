#define SQR(x) ((x) * (x))

int compute(int v)
{
    return SQR(v);
}

#define SQR(x) ((x) * (x) + 1) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-5]

int main()
{
    int result = compute(3) + SQR(2);
    (void)result;
    return 0;
}
