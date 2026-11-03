enum class TaskState { Ready = 0, Running, Finished };

int main()
{
    TaskState state = TaskState::Running;
    unsigned int attempts = 3u;
    return (state == TaskState::Running && attempts == 3u) ? 0 : 1;
}
