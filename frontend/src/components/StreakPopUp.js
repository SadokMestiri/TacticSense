import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';

const StreakPopUp = ({currentStreak}) => {
  const totalDays = 7;
  const [step, setStep] = useState(0);
  const navigate = useNavigate();

  useEffect(() => {
    if (currentStreak >= 1 && currentStreak <= totalDays) {
      setStep(currentStreak);
    }
  }, [currentStreak]);

  const handleClose = () => {
    navigate('/Home');
  };

  const renderRewardBox = (day, content) => {
    const isActive = step >= day;
    return (
      <div
        key={day}
        className={`rewardbox rewarbox_${day} ${isActive ? 'is-active' : ''}`}
          style={{
    transform: 'scale(0.85)',
  }}
      >
        <div className="front">
          <div className="rewardbox-text">Day {day}</div>
          {content.front}
        </div>
        <div className="back">
          <div className="rewardbox-text">Day {day}</div>
          <div className="rewardbox-image">
            <div className="dropshadow-base ">
              <img
                src="https://gloot.netlify.app/images/prototype/reward_check.png"
                height="auto"
                alt=""
              />
            </div>
          </div>
        </div>
      </div>
    );
  };

  const rewards = [
    {
      front: (
        <div className="rewardbox-imagecontainer is-token">
          <div className="rewardbox-image">
            <div className="dropshadow-base  floatingimage">
              <img src="https://gloot.netlify.app/images/prototype/Square_token.png" alt="" />
              <img src="https://gloot.netlify.app/images/prototype/Square_token.png" alt="" />
            </div>
          </div>
        </div>
      ),
    },
    {
      front: (
        <div className="rewardbox-imagecontainer is-coin">
          <div className="rewardbox-image">
            <div className="dropshadow-base  floatingimage">
              <img src="https://gloot.netlify.app/images/prototype/Square_coin.png" alt="" />
              <img src="https://gloot.netlify.app/images/prototype/Square_coin.png" alt="" />
            </div>
          </div>
        </div>
      ),
    },
    {
      front: (
        <div className="rewardbox-imagecontainer is-token">
          <div className="rewardbox-image">
            <div className="dropshadow-base  floatingimage">
              <img src="https://gloot.netlify.app/images/prototype/Square_token.png" alt="" />
              <img src="https://gloot.netlify.app/images/prototype/Square_token.png" alt="" />
            </div>
          </div>
        </div>
      ),
    },
    {
      front: (
        <div className="rewardbox-imagecontainer is-coin">
          <div className="rewardbox-image">
            <div className="dropshadow-base  floatingimage">
              <img src="https://gloot.netlify.app/images/prototype/Square_coin.png" alt="" />
              <img src="https://gloot.netlify.app/images/prototype/Square_coin.png" alt="" />
            </div>
          </div>
        </div>
      ),
    },
    {
      front: (
        <div className="rewardbox-imagecontainer is-token">
          <div className="rewardbox-image">
            <div className="dropshadow-base  floatingimage">
              <img src="https://gloot.netlify.app/images/prototype/Square_token.png" alt="" />
              <img src="https://gloot.netlify.app/images/prototype/Square_token.png" alt="" />
            </div>
          </div>
        </div>
      ),
    },
    {
      front: (
        <div className="rewardbox-imagecontainer is-coin">
          <div className="rewardbox-image">
            <div className="dropshadow-base  floatingimage">
              <img src="https://gloot.netlify.app/images/prototype/Square_coin.png" alt="" />
              <img src="https://gloot.netlify.app/images/prototype/Square_coin.png" alt="" />
            </div>
          </div>
        </div>
      ),
    },
    {
      front: (
        <>
          <div className="rewardbox-imagecontainer is-coin">
            <div className="rewardbox-image">
              <div className="dropshadow-base floatingimage">
                <img src="https://gloot.netlify.app/images/prototype/Square_coin.png" alt="" />
                <img src="https://gloot.netlify.app/images/prototype/Square_coin.png" alt="" />
              </div>
            </div>
          </div>
        </>
      ),
    },
  ];

  return (
          <div className='grid-container'>
    <div className="absolute inset-0 flex justify-center items-center  bg-opacity-60 z-50">
      <div className="relative w-full max-w-sm p-4 bg-white rounded-lg shadow-lg">
        {/* Content */}
        <div className="flex flex-col space-y-4">
          <div className="dailyreward-content grid grid-cols-2 gap-2">
            {rewards.map((reward, idx) => renderRewardBox(idx + 1, reward))}
          </div>
        </div>
            <div className="flex justify-center">
      <button className="button is-glowing mt-4 next_step" style={{cursor:"pointer",marginTop:"20px"}} onClick={handleClose}>
        <span>Close</span>
      </button>
    </div>
      </div>
    </div>
    </div>
  );
};

export default StreakPopUp;
