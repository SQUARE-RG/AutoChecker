enum Status { idle = 0, busy = 1 };

int main()
{
    unsigned int counter = 0;
    Status status = idle;
    counter += 5;
    counter += 7;
    status = busy;
    return static_cast<int>(status);
}
