enum Priority
{
    PriorityLow = 0,
    PriorityHigh = 1
};

struct TaskInfo
{
    Priority priority;
    unsigned int retryCount;
};

int main()
{
    TaskInfo info{};
    info.priority = PriorityHigh;
    info.retryCount = 2u;
    return 0;
}
