struct ThreadState
{
    static thread_local int value;
};

thread_local int ThreadState::value = 0;

int main()
{
    ThreadState::value = 1;
    return 0;
}
