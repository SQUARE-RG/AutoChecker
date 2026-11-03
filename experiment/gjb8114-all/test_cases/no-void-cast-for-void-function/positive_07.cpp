struct Action
{
    void operator()(int) const
    {
    }
};

int main()
{
    Action action;
    action(7);
    return 0;
}
