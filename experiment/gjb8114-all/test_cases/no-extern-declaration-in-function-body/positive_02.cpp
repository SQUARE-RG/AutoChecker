int shared_data = 7;

int add_one(int value)
{
    return value + 1;
}

int main()
{
    static int call_count = 0;
    int local = add_one(shared_data);
    ++call_count;
    return local + call_count;
}
