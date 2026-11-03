int global_limit = 10;

int clamp_to_limit(int)
{
    return global_limit;
}

int main()
{
    return clamp_to_limit(42);
}
