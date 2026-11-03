int Gstate = 0;

void wait_for_ready()
{
    while(1)
    {
        if (Gstate != 0)
        {
            goto done;
        }
    }
done:
    return;
}

int main()
{
    wait_for_ready();
    return 0;
}
