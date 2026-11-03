int main()
{
    int observed = 7;
    return observed - 7;
}

static int unused_default_sum(int lhs, int rhs = 1) { return lhs + rhs; } // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-7-13]
