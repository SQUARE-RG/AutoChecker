enum WorkState
{
    WorkIdle = 0,
    WorkBusy = 1
};

int main()
{
    WorkState state = WorkBusy;
    int count = 3;
    const int& countRef = count;
    (void)state;
    (void)countRef;
    return 0;
}
