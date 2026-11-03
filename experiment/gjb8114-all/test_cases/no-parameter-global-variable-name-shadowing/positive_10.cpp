int limit = 10;

void set_limit(int new_limit = 5)
{
    limit = new_limit;
}

int main()
{
    set_limit();
    return limit;
}
