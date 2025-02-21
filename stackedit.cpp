#include <sys/resource.h>
#include <cstdio>
#include <stdlib.h>


int main (int argc, char **argv)
{
    const rlim_t kStackSize = 32 * 1024 * 1024 * 1024;   // min stack size = 16 MB
    struct rlimit rl;
    int result;

    result = getrlimit(RLIMIT_STACK, &rl);
    if (result == 0)
    {
        if (rl.rlim_cur < kStackSize)
        {
            rl.rlim_cur = kStackSize;
            result = setrlimit(RLIMIT_STACK, &rl);
            if (result != 0)
            {
                printf("%f",stderr, "setrlimit returned result = %d\n", result);
            }
        }
    }

    // ...

    return 0;
}