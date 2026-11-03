enum class Status : int
{
    Idle,
    Running = 1, // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-11-4]
    Stopped
};

int main()
{
    Status s = Status::Stopped;
    return static_cast<int>(s);
}
