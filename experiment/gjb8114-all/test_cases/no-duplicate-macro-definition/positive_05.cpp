#ifdef USE_METRIC
#define DISTANCE_UNIT 10
#endif

#ifndef USE_METRIC
#define DISTANCE_UNIT 20
#endif

int main()
{
    int distance = DISTANCE_UNIT;
    return distance;
}
