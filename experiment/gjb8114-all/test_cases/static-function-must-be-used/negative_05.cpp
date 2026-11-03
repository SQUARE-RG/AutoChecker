namespace {
static int unused_anonymous_helper(int value) { return value + 1; } // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-7-13]
}

int main()
{
    return 0;
}
