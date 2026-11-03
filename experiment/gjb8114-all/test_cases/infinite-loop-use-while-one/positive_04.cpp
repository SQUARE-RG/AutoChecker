namespace
{
    int poll_state()
    {
        int state = 0;

        while(1)
        {
            switch (state)
            {
                case 0:
                    state = 1;
                    break;
                default:
                    return state;
            }
        }
    }
}

int main()
{
    return poll_state();
}
