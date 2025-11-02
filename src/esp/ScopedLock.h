class ScopedLock {
  private:
    bool* lLock;
  public:
  ScopedLock(portMUX_TYPE* spinLock, bool* lock) {
    //first, wait for the boolean lock to indicate it is free. then, if is free, use the spinlock to acquire it as fast as possible
    //if the lock is acquired during the time we detect the lock being free and try to reclaim it in the spinlock, then we will back out and try again
    bool success = false;
    while (true) {
      while (*lock);
      taskENTER_CRITICAL(spinLock);
      //not that we are in the critical section, quickly check to see if the lock is freed. if it is freed, then acquire it. otherwise, leave the critical section and try again
      if (!(*lock)) {
        *lock = true;
        lLock = lock;
        success = true;
      }
      taskEXIT_CRITICAL(spinLock);
      if (success) break;
    }
  }

  ~ScopedLock() {
    //critical section isnt needed to free the lock, so just free it
    *lLock = false;
  }
};