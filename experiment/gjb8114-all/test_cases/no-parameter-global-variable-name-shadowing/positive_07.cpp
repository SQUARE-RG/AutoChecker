int argc = 0;
int count_args(int count, ...)
{
    argc = count;
    return argc;
}
int main()
{
    return count_args(6);
}
