import React from 'react';

const NewsScroller = () => {
  // Sample data for demonstration
  const actions = [
    { instrument: 'ACC', datetime: '01:12:2024 11:30', action: 'IV >=5%' },
    // Add more items as needed
  ];

  return (
    <div className='flex flex-col h-[70vh] border-2 mr-5 border-gray-500 rounded-lg overflow-hidden'>
      <div className='flex justify-center p-3 bg-[#072f3f] text-white'>
        <h1 className='text-lg font-bold'>Instrument Actions</h1>
      </div>

      <div className='flex-1 overflow-auto'>
        <table className='min-w-full border-collapse bg-white'>
          <thead>
            <tr className='bg-gray-200'>
              <th className='border border-gray-400 p-2 text-left'>Instrument</th>
              <th className='border border-gray-400 p-2 text-left'>DateTime</th>
              <th className='border border-gray-400 p-2 text-left'>Action</th>
            </tr>
          </thead>
          <tbody>
            {actions.length > 0 ? (
              actions.map((action, index) => (
                <tr key={index} className='hover:bg-gray-100'>
                  <td className='border border-gray-400 p-2'>{action.instrument}</td>
                  <td className='border border-gray-400 p-2'>{action.datetime}</td>
                  <td className='border border-gray-400 p-2'>{action.action}</td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="3" className='border border-gray-400 p-2 text-center text-gray-600'>
                  No actions available.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default NewsScroller;
