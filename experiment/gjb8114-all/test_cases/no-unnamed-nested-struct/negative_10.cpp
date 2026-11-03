struct Task
{
    struct Context { using Id = unsigned int; }; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-9]
};

int main()
{
    Task task{};
    (void)task;
    return 0;
}
