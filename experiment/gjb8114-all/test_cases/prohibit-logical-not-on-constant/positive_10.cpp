struct State
{
    bool flag;
};

int main()
{
    State s{false};
    if (!s.flag)
    {
        s.flag = true;
    }
    return s.flag ? 0 : 1;
}
