struct Action
{
    void operator()(int) const
    {
    }
};

int main()
{
    Action action;
    (void)action(7); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-7-12]
    return 0;
}
