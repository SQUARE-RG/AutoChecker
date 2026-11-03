int pick(int* lower, int* upper)
{
    return (lower <= upper) ? // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-12-2]
        1 : 0;
}
