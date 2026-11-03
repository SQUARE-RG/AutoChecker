int next_id()
{
    thread_local int counter = 0;
    counter = counter + 1;
    return counter;
}

int main()
{
    return next_id();
}
