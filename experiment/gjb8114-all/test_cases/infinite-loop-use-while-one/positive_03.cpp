#include <iostream>

class Worker
{
public:
    int run(int limit)
    {
        int count = 0;

        while(1)
        {
            if (count >= limit)
            {
                return count;
            }
            ++count;
        }
    }
};

int main()
{
    Worker worker;
    return worker.run(3);
}
