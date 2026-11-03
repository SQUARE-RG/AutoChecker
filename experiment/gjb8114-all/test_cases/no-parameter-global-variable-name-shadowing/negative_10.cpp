int limit = 10;

void reset_limit(int limit = 5) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-2]
{
    limit = limit + 1;
}

int main()
{
    reset_limit();
    return limit;
}
