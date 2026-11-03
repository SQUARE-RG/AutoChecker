struct Worker
{
    void process(int value)
    {
        int local = value + 1;
        (void)local;
    }
};

int main()
{
    Worker worker;
    void (Worker::*member)(int) = &Worker::process;
    (void)(worker.*member)(5); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-7-12]
    return 0;
}
