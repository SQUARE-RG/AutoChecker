#define LOOP for // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-2]

int main()
{
    int sum = 0;
    LOOP (int i = 0; i < 3; ++i)
    {
        sum += i;
    }
    return sum;
}
