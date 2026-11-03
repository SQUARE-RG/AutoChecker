int main()
{
    int sum = 0;
    for (int i = 0; i < 10; /* outer loop-header comment
                               /* nested loop-header comment
                            */ ++i) { // CHECK-MESSAGES: :[[@LINE-1]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-2-6]
        sum += i;
    }
    return sum;
}
