int counter = 0;

void reset_to_start(int start)
{
    int counter = start;
    counter += 1;
    (void)counter;
}

int main()
{
    reset_to_start(3);
    return 0;
}
