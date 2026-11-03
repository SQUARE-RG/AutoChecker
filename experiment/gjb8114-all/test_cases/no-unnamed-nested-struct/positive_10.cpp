struct Task
{
    struct Context { using Id = unsigned int; } *context;
};

int main()
{
    Task task{};
    Task::Context ctx{};
    task.context = &ctx;
    Task::Context::Id id = 7;
    (void)id;
    return 0;
}
