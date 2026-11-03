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
    (worker.*member)(5);
    return 0;
}
