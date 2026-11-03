void process(void)
{
}

int main()
{
    int values[] = {1, 2};
    for (int process : values) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-3]
        (void)process;
    }
    return 0;
}
